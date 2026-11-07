package mcdiamond.mixin;

import net.minecraft.class_2540;
import net.minecraft.class_2817;
import net.minecraft.class_2960;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(value = class_2817.class, remap = false)
public interface StepPayloadAccess {
    @Accessor(value = "field_12830", remap = false)
    class_2960 mcdiamondChannel();

    @Accessor(value = "field_12832", remap = false)
    class_2540 mcdiamondData();
}
